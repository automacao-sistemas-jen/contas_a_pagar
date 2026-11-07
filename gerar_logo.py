from PIL import Image, ImageDraw, ImageFont
import os

# Cria a pasta se não existir
if not os.path.exists("static"):
    os.makedirs("static")

# Configurações da imagem (500x500 pixels)
width, height = 500, 500
bg_color = (30, 30, 30) # Fundo escuro (#1E1E1E)
text_j_color = (255, 215, 0) # Dourado (#FFD700)
text_c_color = (255, 255, 255) # Branco

# Cria a imagem com fundo transparente
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Desenha o quadrado arredondado escuro
draw.rounded_rectangle((10, 10, width-10, height-10), radius=80, fill=bg_color)

# Carrega as fontes (Arial Bold para ficar forte)
try:
    font_jen = ImageFont.truetype("arialbd.ttf", 190)
    font_sub = ImageFont.truetype("arialbd.ttf", 40)
except IOError:
    font_jen = ImageFont.load_default()
    font_sub = ImageFont.load_default()

# Função auxiliar para centralizar o texto
def draw_centered_text(texto, fonte, y_pos, cor):
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    text_width = bbox[2] - bbox[0]
    x_pos = (width - text_width) / 2
    draw.text((x_pos, y_pos), texto, font=fonte, fill=cor)

# Desenha o JEN e o subtítulo
draw_centered_text("JEN", font_jen, 120, text_j_color)
draw_centered_text("CONTAS A PAGAR", font_sub, 350, text_c_color)

# Salva a imagem
img.save("static/logo_contas.png")
print("Logo criado com sucesso em: static/logo_contas.png")