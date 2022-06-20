import pygame

#dopasowanie rozmiaru obrazu
def scale_image (img, factor):
    size = round(img.get_width()* factor), round(img.get_height()* factor)
    return pygame.transform.scale(img, size)

#jazda autem
def blit_rotate_centrer(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle) #w pygame obraz jest prostokątem i sie obraca na wokół lewego górnego rogu
    new_rect = rotated_image.get_rect (center=image.get_rect(topleft = top_left).center) # przeniesienie na srodek punktu, wg którego obraz bedzie się obracał
    win.blit(rotated_image, new_rect.topleft)

#funkcja do wyświetlania tekstu
def blit_text_center(win, font, text):
    render = font.render(text, 1, (0, 0, 0))
    win.blit (render, (200, 300))
    #win.blit (render, (win.get_width()/2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2 ))