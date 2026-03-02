"""
Management command to seed demo data for the Grievance Management System.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from grievance_portal.models import User, Complaint, ComplaintTimeline, DuplicateMapping
from ai_engine import ai_engine


SAMPLE_COMPLAINTS = [
    ("Pothole on MG Road near Bus Stop", "There is a large pothole on MG Road near the main bus stop. It has been there for over 2 months and has caused multiple accidents. Vehicles are getting damaged and citizens are at risk. Need immediate repair."),
    ("No water supply for 4 days", "Our area has not received any water supply for the past 4 days. Residents are suffering greatly, especially elderly people and children. The municipal helpline is not responding. This is a severe water shortage emergency."),
    ("Overflowing drainage near school", "The drainage near City Primary School is overflowing causing sewage water to flood the road. Children are having to wade through dirty water. This is a serious health hazard. Immediate action required."),
    ("Street lights not working in Sector 7", "All street lights in Sector 7 colony have not been working for 3 weeks. The area is completely dark at night making it unsafe for residents, especially women returning home late."),
    ("Garbage pile near community park", "There is a massive pile of uncollected garbage near the community park. It has been rotting for a week and is causing a terrible smell and attracting flies and rats. Health hazard for nearby residents."),
    ("Road broken after rain", "Heavy rain has severely damaged the road on Gandhi Nagar Main Road. Multiple sections have collapsed and vehicles are getting stuck. People are forced to take long alternate routes."),
    ("Contaminated water supply", "The drinking water supplied by the municipal authority has a foul smell and appears brownish. Multiple residents have fallen ill due to stomach problems. Water quality testing needed urgently."),
    ("Illegal construction blocking road", "An unauthorized construction is blocking 50% of the road width on our street. Emergency vehicles cannot pass through. The builder has ignored all complaints."),
    ("Traffic signal malfunction at Junction", "The traffic signal at Main Market Junction has been malfunctioning for 5 days. This is causing severe traffic jams during peak hours and risk of accidents. Please fix urgently."),
    ("Park benches destroyed by vandals", "The benches in Central Park have been vandalized and broken. Sharp metal pieces are exposed, posing risk of injury to children. The park is used by many families in evenings."),
    ("Electricity pole fallen on road", "An electricity pole has fallen on the main road near the hospital. Live wires are hanging dangerously. Multiple near-miss incidents have been reported. EXTREMELY URGENT - risk of electrocution."),
    ("Manhole cover missing - dangerous", "A manhole cover is missing on the busy road near the market. A child nearly fell into it yesterday. This is extremely dangerous especially at night. Immediate action needed."),
    ("Noise pollution from construction at night", "The construction site adjacent to our residential colony carries out loud construction work even after 10 PM, violating noise pollution norms. Residents cannot sleep. Children and elderly are being severely affected."),
    ("Stray dogs attacking residents", "A pack of aggressive stray dogs in our locality has been attacking residents. Three people have been bitten this week. Animal control needs to be dispatched immediately."),
    ("Water pipeline burst flooding street", "The main water pipeline has burst near Nehru Street flooding the entire road. Water is being wasted and the road has become completely waterlogged making it impassable."),
]


class Command(BaseCommand):
    help = 'Seeds the database with demo data including users and complaints'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            ComplaintTimeline.objects.all().delete()
            DuplicateMapping.objects.all().delete()
            Complaint.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating demo users...')

        # Admin user
        admin, created = User.objects.get_or_create(username='admin')
        if created or True:
            admin.set_password('admin123')
            admin.email = 'admin@smartgriev.gov.in'
            admin.first_name = 'System'
            admin.last_name = 'Administrator'
            admin.role = 'admin'
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('  ✓ Admin: admin / admin123'))

        # Citizens
        citizens = []
        citizen_data = [
            ('citizen', 'citizen123', 'Rahul', 'Sharma', 'rahul@example.com'),
            ('priya', 'priya123', 'Priya', 'Verma', 'priya@example.com'),
            ('arun', 'arun123', 'Arun', 'Kumar', 'arun@example.com'),
        ]

        for uname, pwd, fname, lname, email in citizen_data:
            user, created = User.objects.get_or_create(username=uname)
            user.set_password(pwd)
            user.email = email
            user.first_name = fname
            user.last_name = lname
            user.role = 'citizen'
            user.save()
            citizens.append(user)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Citizen: {uname} / {pwd}'))

        self.stdout.write('Creating sample complaints with AI analysis...')

        statuses = ['submitted', 'under_review', 'in_progress', 'resolved', 'submitted', 'in_progress']
        locations = [
            (17.3850, 78.4867), (17.4401, 78.4982), (17.3616, 78.4747),
            (17.4156, 78.4347), (17.3279, 78.5518), (17.4947, 78.3996),
            (17.3753, 78.4744), (17.4239, 78.4738), (17.3512, 78.4867),
            (None, None), (None, None),
        ]

        for i, (title, desc) in enumerate(SAMPLE_COMPLAINTS):
            user = random.choice(citizens)
            ai_result = ai_engine.process_complaint(title, desc, [])

            lat, lng = random.choice(locations)

            created_days_ago = random.randint(1, 30)
            created_at = timezone.now() - timedelta(days=created_days_ago)

            status = random.choice(statuses)

            complaint = Complaint.objects.create(
                user=user,
                title=title,
                description=desc,
                category=ai_result['category'],
                priority_score=ai_result['priority_score'],
                priority_level=ai_result['priority_level'],
                sentiment_score=ai_result['sentiment_score'],
                sentiment_label=ai_result['sentiment_label'],
                estimated_resolution_days=ai_result['estimated_resolution_days'],
                expected_resolution_date=ai_result['expected_resolution_date'],
                status=status,
                latitude=lat,
                longitude=lng,
                location_address='Hyderabad, Telangana' if lat else '',
            )

            # Fix created_at (override auto_now_add)
            Complaint.objects.filter(id=complaint.id).update(created_at=created_at)

            if status == 'resolved':
                resolved_at = created_at + timedelta(days=random.randint(1, 10))
                Complaint.objects.filter(id=complaint.id).update(
                    resolved_at=resolved_at
                )

            # Add timeline
            ComplaintTimeline.objects.create(
                complaint=complaint,
                status='submitted',
                message='Complaint submitted and AI analysis completed.',
                updated_by=user,
            )
            ComplaintTimeline.objects.filter(complaint=complaint).update(
                timestamp=created_at
            )

            if status in ['under_review', 'in_progress', 'resolved']:
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status='under_review',
                    message='Complaint reviewed by admin and assigned to department.',
                    updated_by=admin,
                )

            if status in ['in_progress', 'resolved']:
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status='in_progress',
                    message='Work order issued. Field team dispatched to location.',
                    updated_by=admin,
                )

            if status == 'resolved':
                ComplaintTimeline.objects.create(
                    complaint=complaint,
                    status='resolved',
                    message='Issue has been resolved. Please verify and close.',
                    updated_by=admin,
                )

            self.stdout.write(f'  ✓ Complaint: [{ai_result["category"].upper()}] {title[:50]}...')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(self.style.SUCCESS('  Admin:   username=admin, password=admin123'))
        self.stdout.write(self.style.SUCCESS('  Citizen: username=citizen, password=citizen123'))
        self.stdout.write(self.style.SUCCESS('  URL: http://127.0.0.1:8000'))
