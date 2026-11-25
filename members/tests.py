from django.test import TestCase, Client
from django.urls import reverse
from .models import Flat, Guest, RentalStatus, Vehicle


class MembersModelTests(TestCase):
    def setUp(self):
        self.flat = Flat.objects.create(flat_number="101", wing="A")

    def test_flat_slug_generated(self):
        self.assertEqual(self.flat.slug, "101A")
        self.assertEqual(str(self.flat), "101 A")

    def test_guest_creation(self):
        guest = Guest.objects.create(
            flat_number=self.flat,
            first_name="John",
            last_name="Doe",
            mobile="9876543210"
        )
        self.assertEqual(guest.full_name(), "John Doe")
        self.assertEqual(str(guest), "John Doe")

    def test_rental_status(self):
        rental = RentalStatus.objects.create(flat_number=self.flat, is_rented=False)
        self.assertEqual(str(rental), "Not Rented")
        rental.is_rented = True
        rental.save()
        self.assertEqual(str(rental), "Rented")


class MembersViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.flat = Flat.objects.create(flat_number="101", wing="A")
        self.guest = Guest.objects.create(
            flat_number=self.flat,
            first_name="Jane",
            last_name="Smith",
            mobile="9123456789"
        )
        self.rental = RentalStatus.objects.create(flat_number=self.flat, is_rented=False)

    def test_home_view_standard(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertContains(response, "Society Members")

    def test_home_view_htmx_search(self):
        response = self.client.get(
            reverse('home') + "?q=Jane",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Smith")
        self.assertTemplateUsed(response, "members/partials/guest_rows.html")

    def test_home_view_htmx_search_no_match(self):
        response = self.client.get(
            reverse('home') + "?q=NonExistentName",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No members found")

    def test_delete_view_htmx(self):
        response = self.client.delete(
            reverse('delete', kwargs={'pk': self.guest.id}),
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "")
        self.assertFalse(Guest.objects.filter(id=self.guest.id).exists())

    def test_flat_view_standard(self):
        response = self.client.get(reverse('all_flats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Flat 101")

    def test_flat_view_htmx_filter(self):
        response = self.client.get(
            reverse('all_flats') + "?wing=A",
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "members/partials/flat_cards.html")
        self.assertContains(response, "Flat 101")

    def test_flat_detail_view(self):
        response = self.client.get(reverse('flat_detail', kwargs={'slug': self.flat.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wing A")
        self.assertContains(response, "Jane Smith")

    def test_toggle_rental_status_htmx(self):
        self.assertFalse(self.rental.is_rented)
        response = self.client.post(
            reverse('toggle_rental', kwargs={'slug': self.flat.slug}),
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.rental.refresh_from_db()
        self.assertTrue(self.rental.is_rented)
        self.assertContains(response, "Rented Flat")

    def test_add_and_delete_vehicle_htmx(self):
        response = self.client.post(
            reverse('add_vehicle', kwargs={'slug': self.flat.slug}),
            data={
                'vehicle': 'FWST',
                'registration_number': 'mh 02 ab 1234',
                'make': 'Honda',
                'model': 'City',
            },
            headers={"HX-Request": "true"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.flat.vehicle_set.count(), 1)
        vehicle = self.flat.vehicle_set.first()
        self.assertEqual(vehicle.registration_number, 'MH 02 AB 1234')
        self.assertEqual(vehicle.make, 'Honda')
        self.assertEqual(vehicle.model, 'City')
        self.assertContains(response, 'MH 02 AB 1234')
        self.assertContains(response, 'Honda City')

        del_response = self.client.delete(
            reverse('delete_vehicle', kwargs={'pk': vehicle.id}),
            headers={"HX-Request": "true"}
        )
        self.assertEqual(del_response.status_code, 200)
        self.assertEqual(self.flat.vehicle_set.count(), 0)

    def test_add_vehicle_bh_series_and_invalid_format(self):
        bh_response = self.client.post(
            reverse('add_vehicle', kwargs={'slug': self.flat.slug}),
            data={'vehicle': 'TWST', 'registration_number': '22 BH 1234 AB'},
            headers={"HX-Request": "true"}
        )
        self.assertEqual(bh_response.status_code, 200)
        self.assertEqual(self.flat.vehicle_set.count(), 1)

        bad_response = self.client.post(
            reverse('add_vehicle', kwargs={'slug': self.flat.slug}),
            data={'vehicle': 'FWST', 'registration_number': 'INVALID123'},
            headers={"HX-Request": "true"}
        )
        self.assertEqual(bad_response.status_code, 200)
        self.assertEqual(self.flat.vehicle_set.count(), 1)
        self.assertContains(bad_response, 'Enter a valid Indian vehicle registration number')
