# -*- coding: utf-8 -*-
"""SEMEX_Telegram_Bot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1is6PrZ6zHEkb4HfB_UEstegQiDiWguIF
"""

!pip install requests aiogram qrcode

from typing import Any, Dict
import qrcode

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile
from io import BytesIO
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

#Token do Bot
TOKEN = '6603278502:AAHwo4jp0e2ejNnah-n7MDp38-cFnP5QZhY'

#Criando o Router
form_router = Router()

#Definindo os estados do bot
class Form(StatesGroup):
    pergunta_gerar_qr_code = State()
    quer_qr_code = State()

#Função para gerar o QrCode
def gerarQrCode(texto):
    qr = qrcode.make(texto)
    temp = BytesIO()
    # Salva o qr code em um arquivo temporário
    qr.save(temp)
    temp.seek(0)
    # Cria um arquivo para enviar
    file_to_send = BufferedInputFile(temp.getvalue(), "qrcode.png")
    return file_to_send

#Comando de Inicio
@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    # Define o proximo estado do bot
    await state.set_state(Form.pergunta_gerar_qr_code)

#Mensagem de Inicio
    await message.answer('Fala meu cria, quer gerar um qr code? Se sim, digite /sim, se não, digite /nao',
            # Cria um teclado com as opções de sim e não
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="/Sim"), KeyboardButton(text="/Não")]
            ],
            resize_keyboard=True,
        ),
    )

#Mensagem caso o usuário não queira gerar um QrCode
@form_router.message(Form.pergunta_gerar_qr_code, F.text.casefold() == ("/nao" or "/não"))
async def process_dont_want_qr_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    # Mensagem de agradecimento
    await message.answer(
        "'Obrigado pela visita, mano!\nVolte sempre!'",
        reply_markup=ReplyKeyboardRemove(),
    )

    # Mostra o resumo
    await show_summary(message=message, data=data, positive=False)


#Mensagem caso o usuário queira gerar um QrCode
@form_router.message(Form.pergunta_gerar_qr_code, F.text.casefold() == "/sim")
async def process_want_qr_code(message: Message, state: FSMContext) -> None:
    # Define o proximo estado do bot
    await state.set_state(Form.quer_qr_code)

    # Pergunta o que o usuário deseja fazer e espera a resposta
    await message.reply(
        'Boa, mano! Agora ta na hora de digitar uma mensagem, texto ou link que queira o QRCode.'
                      + '\nPara parar, digite /pronto e a gente termina por aqui.',
        reply_markup=ReplyKeyboardRemove(),
    )

#Mensagem caso o usuário digite uma opção inválida
@form_router.message(Form.pergunta_gerar_qr_code)
async def process_unknown_options(message: Message) -> None:
    await message.reply("Escolha uma opção válida.")

#Mensagem caso o usuário digite um texto ou link válido
@form_router.message(Form.quer_qr_code, F.text.casefold() != ("/pronto" or "pronto"))
async def process_quer_qr_code(message: Message, state: FSMContext) -> None:

    # Pega os dados do estado atual
    data = await state.get_data()
    # Pega o número de qr codes gerados
    qr_code_numbers = int(data.get("qr_code_numbers", 0))

    # Verifica se o texto é válido
    if message.text is not None:
        # Gera o qr code
        qr_code = gerarQrCode(message.text)
        await message.reply("Aqui está o seu QR Code:", reply_markup=ReplyKeyboardRemove())
        # Assuming `qr_code` is the QR code image data

        # Envia o qr code
        await message.answer_photo(qr_code, caption="Seu QR Code")
        await state.update_data(qr_code_numbers=(qr_code_numbers + 1))

        # Pergunta se o usuário deseja criar outro qr code
        await message.reply("Paizão, se você deseja criar outro QR Code, digite o link ou texto que deseja transformar em QR Code ou digite /pronto se desejar parar.")
    else:
        await message.reply('Essa opção não existe, meu cria!')

@form_router.message(Form.quer_qr_code, F.text.casefold() == ("/pronto"))
async def process_end_qr_code(message: Message, state: FSMContext) -> None:
    # Pega os dados do estado atual
    data = await state.get_data()

    # Mostra o resumo
    await state.clear()
    await message.reply("Ok, você não quer criar um QR Code.", reply_markup=ReplyKeyboardRemove())
    await show_summary(message=message, data=data, positive=True)



#Função para mostrar o resumo
async def show_summary(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    # Mensagem de resumo
    text = f"Parabéns, por gerar {data['qr_code_numbers']} QRCodes, mano!" if 'qr_code_numbers' in data else ""
    # Mensagem de agradecimento
    if positive:
        text += '\nValeu pela visita, mano!'
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    else:
        text += '\nPooo, que pena que você nao quis gerar nada, mas valeu pela visita, meu cria!'
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())




#Função principal
async def main():
    # Cria o bot
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    # Cria o dispatcher
    dp = Dispatcher()
    # Adiciona o router ao dispatcher
    dp.include_router(form_router)
    # Inicia o bot
    await dp.start_polling(bot)

#Executa a função principal
await main()