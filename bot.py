from aiogram import Bot, Dispatcher, types, F
import asyncio
from aiogram.fsm.context import FSMContext
import aiosqlite
from datebase import Database
from states import RegisterState, AddHospitalState, AddDoctorState
from default_keyboards import phone_btn, location_btn, admin_menu
from geopy import Nominatim
import datetime

geolocator = Nominatim(user_agent="myCLINICBOOKINGAppnimadir")

bot = Bot(token="8416480463:AAHC35GzJXcQcFm0GA9cLxGmyYMf6jALPqE")
dp = Dispatcher()
db = Database()

ADMIN_ID = "5939452056"


@dp.message(F.text == "/start")
async def start_booking(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    print(user)
    if str(user_id) == ADMIN_ID:
        await message.answer("Admin panelga xush kelibsiz!", reply_markup=admin_menu)
    elif user:
        await message.answer("Assalamu alaykum! Xush kelibsiz. Qaysi shifokor turini tanlaysiz?")
    else:
        await message.answer("Iltimos, avval ro'yxatdan o'ting.")
        await message.answer("Ro'yxatdan o'tish uchun ism-familiyangizni kiriting:")
        await state.set_state(RegisterState.full_name)

@dp.message(RegisterState.full_name)
async def full_name_handler(message: types.Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer("Iltimos, telefon raqamingizni yuboring", reply_markup=phone_btn)
    await state.set_state(RegisterState.phone)

@dp.message(RegisterState.phone, F.contact)
async def phone_number_handler(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data(phone_number=phone_number)
    await message.answer("Iltimos, joylashuvingizni yuboring", reply_markup=location_btn)
    await state.set_state(RegisterState.location)   

@dp.message(RegisterState.location, F.location)
async def location_handler(message: types.Message, state: FSMContext):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    addresss = geolocator.reverse((latitude, longitude), exactly_one=True)
    if addresss:
        print(addresss, addresss.address)
        address = addresss.address
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data = await state.get_data()
        full_name = user_data['full_name']
        phone_number = user_data['phone_number']
        user_id = message.from_user.id
        
        # O'ZGARISH: db metodi endi 'await' bilan chaqiriladi
        await db.add_user(user_id, full_name, phone_number, address, latitude, longitude, created_at)
        
        await message.answer(f"Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!\n\nFull Name: {full_name}\nPhone: {phone_number}\nLocation: {address}")
        await state.clear()
    else:
        # O'ZGARISH: Mantiqiy xato tuzatildi. `addresss` None bo'lsa, uning atributiga murojaat qilinmaydi.
        print("Manzilni aniqlab bo'lmadi.")
        await message.answer("Manzilni aniqlab bo'lmadi, iltimos boshqa lokatsiya yuboring.")
        

@dp.message(F.text=='All users')
async def all_users_handler(message: types.Message):
    # O'ZGARISH: db metodi endi 'await' bilan chaqiriladi (nomi ham o'zgargan)
    await db.all_users_to_excel()
    
    users = types.FSInputFile("users.xlsx")
    await message.answer_document(document=users)

@dp.message(F.text=='Add hospital')
async def add_hospital_start(message: types.Message, state: FSMContext):
    await message.answer("Iltimos, shifoxona nomini kiriting:")
    await state.set_state(AddHospitalState.name)

@dp.message(AddHospitalState.name)
async def hospital_name_handler(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Iltimos, shifoxona manzilini kiriting:", reply_markup=location_btn)
    await state.set_state(AddHospitalState.address)


@dp.message(AddHospitalState.address, F.location)
async def hospital_address_handler(message: types.Message, state: FSMContext):
    location = message.location
    latitude = location.latitude
    longitude = location.longitude
    addresss = geolocator.reverse((latitude, longitude), exactly_one=True)
    if addresss:
        print(addresss, addresss.address)
        address = addresss.address
        hospital_data = await state.get_data()
        name = hospital_data['name']
        
        # O'ZGARISH: db metodi endi 'await' bilan chaqiriladi
        await db.add_hospital(name, address, latitude, longitude)
        
        await message.answer(f"Shifoxona muvaffaqiyatli qo'shildi!\n\nName: {name}\nAddress: {address}")
        await state.clear()
    else:
        print("Manzilni aniqlab bo'lmadi.")
        await message.answer("Manzilni aniqlab bo'lmadi, iltimos boshqa lokatsiya yuboring.")

@dp.message(F.text=='All hospitals')
async def all_hospitals_handler(message: types.Message):
    # O'ZGARISH: db metodi endi 'await' bilan chaqiriladi (nomi ham o'zgargan)
    await db.all_hospitals_to_excel()
    
    hospitals = types.FSInputFile("hospitals.xlsx")
    await message.answer_document(document=hospitals)

async def add_doctor(self, name, specialty, available_times, hospital_id):
        """Shifokorni bazaga qo'shish"""
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                INSERT INTO doctors (name, specialty, available_times, hospital_id)
                VALUES (?, ?, ?, ?)
            """, (name, specialty, available_times, hospital_id))
            await db.commit()
        print(f"👨‍⚕️ Shifokor qo'shildi: {name}")

async def all_doctors(self):
        """Barcha shifokorlarni chiqarish"""
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("""
                SELECT d.id, d.name, d.specialty, d.available_times, h.name AS hospital_name
                FROM doctors d
                LEFT JOIN hospitals h ON d.hospital_id = h.id
            """) as cursor:
                doctors = await cursor.fetchall()
        if doctors:
            print("👨‍⚕️ Barcha shifokorlar:")
            for d in doctors:
                print(f"ID: {d[0]} | Ism: {d[1]} | Mutaxassislik: {d[2]} | Soatlar: {d[3]} | Shifoxona: {d[4]}")
        else:
            print("⚠️ Shifokorlar topilmadi.")
        return doctors

async def main():
    # O'ZGARISH: Jadvallarni yaratish ham endi asinxron
    await db.create_tables()
    
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())