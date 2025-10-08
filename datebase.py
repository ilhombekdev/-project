import aiosqlite
import pandas as pd
import os
import asyncio # Asinxron funksiyalarni ishga tushirish uchun

class Database:
    def __init__(self, db_name='clinic_booking.db'):
        # `__init__` da ulanish yaratmaymiz, faqat baza nomini saqlaymiz
        self.db_name = db_name

    async def create_tables(self):
        """Barcha jadvallarni asinxron yaratadi."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id VARCHAR(20) UNIQUE,
                                full_name VARCHAR(100),
                                phone VARCHAR(20) UNIQUE,
                                location VARCHAR(255),
                                latitude VARCHAR(30),
                                longitude VARCHAR(30),
                                created_at DATETIME)
            """) # Ustun nomini created_id dan created_at ga o'zgartirdim
            await db.execute("""
                CREATE TABLE IF NOT EXISTS hospitals (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100),
                                address VARCHAR(255),
                                latitude VARCHAR(30),
                                longitude VARCHAR(30))
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS doctors (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name VARCHAR(100),
                                specialty VARCHAR(100),
                                available_times TEXT,
                                hospital_id INTEGER,
                                FOREIGN KEY (hospital_id) REFERENCES hospitals(id))
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id VARCHAR(20),
                    booking_date DATE,
                    booking_time TIME,
                    doctor VARCHAR(100),
                    created_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS doctor_times (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                doctor_id INTEGER,
                                appointment_id INTEGER,
                                FOREIGN KEY (appointment_id) REFERENCES bookings(id),
                                FOREIGN KEY (doctor_id) REFERENCES doctors(id))
            """)
            await db.commit()
    
    async def add_user(self, user_id, full_name, phone, location, latitude, longitude, created_at):
        """Foydalanuvchini bazaga asinxron qo'shadi."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO users (user_id, full_name, phone, location, latitude, longitude, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, full_name, phone, location, latitude, longitude, created_at))
            await db.commit()

    async def get_user(self, user_id):
        """Foydalanuvchini asinxron oladi."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()
    
    async def add_hospital(self, name, address, latitude, longitude):
        """Shifoxonani bazaga asinxron qo'shadi."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO hospitals (name, address, latitude, longitude) 
                VALUES (?, ?, ?, ?)
            """, (name, address, latitude, longitude))
            await db.commit()

    async def all_hospitals_to_excel(self):
        """Barcha shifoxonalarni olib, Excel faylga asinxron yozadi."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM hospitals") as cursor:
                # Ma'lumotlarni va ustun nomlarini olamiz
                hospitals_data = await cursor.fetchall()
                column_names = [description[0] for description in cursor.description]

        if not hospitals_data:
            print("Shifoxonalar topilmadi.")
            return

        # Ma'lumotlarni pandas DataFrame ga o'tkazamiz
        df = pd.DataFrame(hospitals_data, columns=column_names)

        file_name = 'hospitals.xlsx'
        if os.path.exists(file_name):
            os.remove(file_name)
            print("Eski fayl o'chirildi.")
        
        # Excel faylga yozish (bu sinxron operatsiya, lekin bu yerda zarari yo'q)
        df.to_excel(file_name, index=False)
        print(f"Ma'lumotlar {file_name} fayliga muvaffaqiyatli yozildi.")
            
    
    async def add_doctor(self, name, specialty, available_times, hospital_id):
        """Shifokorni bazaga asinxron qo'shadi."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO doctors (name, specialty, available_times, hospital_id) 
                VALUES (?, ?, ?, ?)
            """, (name, specialty, available_times, hospital_id))
            await db.commit()   

    async def get_doctors(self, hospital_id):
        """Shifoxonadagi shifokorlarni asinxron oladi."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM doctors WHERE hospital_id = ?", (hospital_id,)) as cursor:
                return await cursor.fetchall()
    
    async def add_booking(self, user_id, booking_date, booking_time, doctor):
        """Band qilish ma'lumotini asinxron qo'shadi."""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO bookings (user_id, booking_date, booking_time, doctor) 
                VALUES (?, ?, ?, ?)
            """, (user_id, booking_date, booking_time, doctor))
            await db.commit()

    async def get_bookings(self, user_id):
        """Foydalanuvchining band qilgan vaqtlarini asinxron oladi."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM bookings WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchall()
    
    async def all_users_to_excel(self):
        """Barcha foydalanuvchilarni olib, Excel faylga asinxron yozadi."""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM users") as cursor:
                # Ma'lumotlarni va ustun nomlarini olamiz
                users_data = await cursor.fetchall()
                column_names = [description[0] for description in cursor.description]

        if not users_data:
            print("Foydalanuvchilar topilmadi.")
            return

        # Ma'lumotlarni pandas DataFrame ga o'tkazamiz
        df = pd.DataFrame(users_data, columns=column_names)

        file_name = 'users.xlsx'
        if os.path.exists(file_name):
            os.remove(file_name)
            print("Eski fayl o'chirildi.")
        
        # Excel faylga yozish (bu sinxron operatsiya, lekin bu yerda zarari yo'q)
        df.to_excel(file_name, index=False)
        print(f"Ma'lumotlar {file_name} fayliga muvaffaqiyatli yozildi.")


# --- KODNI ISHLATIB KO'RISH UCHUN NAMUNA ---

async def main():
    db = Database()
    
    # 1. Jadvallarni yaratish
    await db.create_tables()
    print("Jadvallar yaratildi yoki mavjud.")
    
    # 2. Test uchun bitta foydalanuvchi qo'shish
    # await db.add_user(
    #     user_id='12345', 
    #     full_name='Test User', 
    #     phone='+998901234567', 
    #     location='Tashkent', 
    #     latitude='41.1', 
    #     longitude='69.2', 
    #     created_at='2025-10-04 14:30:00'
    # )
    # print("Test foydalanuvchi qo'shildi.")

    # 3. Barcha foydalanuvchilarni Excel ga yozish
    await db.all_users_to_excel()

if __name__ == '__main__':
    # Asinxron funksiyani ishga tushirish uchun asyncio.run() ishlatiladi
    asyncio.run(main())