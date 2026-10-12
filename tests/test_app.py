import os
import tempfile
import unittest

from app import create_app


class AseelTests(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(handle)
        self.qr_dir = tempfile.mkdtemp()
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE_PATH": self.db_path,
                "QR_FOLDER": self.qr_dir,
                "SECRET_KEY": "test",
                "ADMIN_EMAIL": "admin@aseel.ae",
                "ADMIN_PASSWORD": "AseelAdmin2026!",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def login(self):
        return self.client.post(
            "/login",
            data={"email": "admin@aseel.ae", "password": "AseelAdmin2026!"},
            follow_redirects=True,
        )

    def test_home_and_seed_verify(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn(b"Authenticity, Verified", home.data)

        authentic = self.client.get("/verify/aseel-royal-oud-001")
        self.assertEqual(authentic.status_code, 200)
        self.assertIn(b"AUTHENTIC PRODUCT", authentic.data)
        self.assertIn(b"Royal Oud", authentic.data)

        fake = self.client.get("/verify/FAKE-999")
        self.assertIn(b"PRODUCT NOT VERIFIED", fake.data)

    def test_scan_warning_and_register(self):
        for _ in range(6):
            self.client.get("/verify/ASEEL-AMBER-NIGHT-003")
        warning = self.client.get("/verify/ASEEL-AMBER-NIGHT-003")
        self.assertIn(b"AUTHENTICITY WARNING", warning.data)

        dashboard = self.login()
        self.assertIn(b"Authentication dashboard", dashboard.data)
        self.assertIn(b"Royal Oud", dashboard.data)

        search = self.client.get("/admin/?q=Royal")
        self.assertIn(b"Royal Oud", search.data)
        self.assertNotIn(b"Desert Musk", search.data)

        detail = self.client.get("/admin/products/1")
        self.assertIn(b"Smart QR Tag", detail.data)

        response = self.client.post(
            "/admin/register",
            data={
                "perfume_name": "Test Rose",
                "brand_name": "ASEEL Demo",
                "batch_number": "BTEST1",
                "box_serial_number": "TEST-UNIQUE-099",
                "manufacturing_date": "2026-10-01",
                "authorized_seller": "ASEEL Lab",
                "place_of_sale": "Khalifa University",
                "status": "Genuine",
                "scan_threshold": "5",
                "notes": "Automated test",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Rose", response.data)
        self.assertIn(b"Smart QR Tag", response.data)

        scans = self.client.get("/admin/scans")
        self.assertEqual(scans.status_code, 200)
        self.assertIn(b"Scan activity", scans.data)

        filtered = self.client.get("/admin/?status=Suspicious")
        self.assertIn(b"<td>Amber Night</td>", filtered.data)
        self.assertNotIn(b"<td>Royal Oud</td>", filtered.data)

        exported = self.client.get("/admin/export.csv")
        self.assertEqual(exported.status_code, 200)
        self.assertIn(b"unique_code", exported.data)
        self.assertIn(b"Royal Oud", exported.data)

        walkthrough = self.client.get("/how-it-works")
        self.assertEqual(walkthrough.status_code, 200)
        self.assertIn(b"How ASEEL works", walkthrough.data)

        missing = self.client.get("/does-not-exist")
        self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
