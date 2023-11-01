import math
import random
import turtle

# side length of each square cell
cell_width = 50
cell_height = 50
# margin of each square cell
cell_margin = 2
# font size
font_size = cell_height // 2

# number of cells in x/y direction
num_cells_x = 8
num_cells_y = 5

# ratio of mined cells
mine_ratio = 0.1

cells = []
mine_remaining = 0
game_in_playing = False


def coordinate_of_cell(x, y):
    """ coordinate of the left-bottom corner of cell x,y """
    posx = (x - (num_cells_x-1) / 2) * cell_width
    posy = (y - (num_cells_y-1) / 2) * cell_height

    return posx, posy


def cell_of_coordinate(posx, posy):
    """ cell at coordinate posx,posy """
    x = posx / cell_width + (num_cells_x - 1) / 2
    y = posy / cell_height + (num_cells_y - 1) / 2

    return math.floor(x), math.floor(y)


def draw_smiley(face):
    turtle.goto(0, (num_cells_y / 2 + 2) * cell_height)
    turtle.setheading(90)
    turtle.shape(face)
    turtle.stamp()


def draw_cell(x, y):
    global game_in_playing

    cell = cells[x+y*num_cells_x]

    if cell['covered']:
        if cell['flagged']:
            turtle.color('yellow')
        elif cell['mine'] and not game_in_playing:
            turtle.color('lightgray')
        else:
            turtle.color('gray')
    else:
        if cell['mine']:
            turtle.color('red')
        else:
            turtle.color('lightgray')

    turtle.penup()
    turtle.goto(coordinate_of_cell(x, y))
    turtle.setheading(90)

    # draw the rectangle
    turtle.begin_fill()
    turtle.pendown()
    turtle.forward(cell_width-cell_margin)
    turtle.right(90)
    turtle.forward(cell_height-cell_margin)
    turtle.right(90)
    turtle.forward(cell_width-cell_margin)
    turtle.right(90)
    turtle.forward(cell_height-cell_margin)
    turtle.penup()
    turtle.end_fill()

    if cell['mine'] and (not cell['flagged']) and (not game_in_playing):
        posx, posy = coordinate_of_cell(x, y)
        turtle.goto(posx + cell_width / 2, posy + cell_height / 2)
        turtle.shape('mine.gif')
        turtle.stamp()

    if cell['flagged'] and cell['covered']:
        posx, posy = coordinate_of_cell(x, y)
        turtle.goto(posx + cell_width / 2, posy + cell_height / 2)
        turtle.shape('flag.gif')
        turtle.stamp()
        # draw a cross for falsely flagged cell
        if not cell['mine'] and (not game_in_playing):
            turtle.color('red')
            turtle.pensize(2)
            turtle.goto(posx, posy)
            turtle.pendown()
            turtle.goto(posx+cell_width, posy+cell_height)
            turtle.penup()
            turtle.goto(posx, posy+cell_height)
            turtle.pendown()
            turtle.goto(posx+cell_width, posy)
            turtle.penup()

    if cell['mine_neighbor'] and not cell['covered'] and not cell['mine']:
        turtle.color('black')
        turtle.goto(coordinate_of_cell(x, y))
        turtle.setheading(0)
        turtle.forward(cell_width/2)
        turtle.setheading(90)
        turtle.write('%s' % cell['mine_neighbor'], align='center', font=('Monospace', font_size, 'bold'))


def draw_field():
    for y in range(num_cells_y):
        for x in range(num_cells_x):
            draw_cell(x, y)


def create_game():
    global cells, mine_remaining
    cells = []
    mine_cells = []
    for i in range(int(mine_ratio * num_cells_x * num_cells_y)):
        mine_cells.append(random.randint(0, num_cells_x * num_cells_y - 1))

    for y in range(num_cells_y):
        for x in range(num_cells_x):
            cells.append({'mine': x + y * num_cells_x in mine_cells, 'covered': True, 'flagged': False, 'mine_neighbor': 0})

    mine_remaining = len(mine_cells)

    for y in range(num_cells_y):
        for x in range(num_cells_x):
            if cells[x + y * num_cells_x]['mine']:
                continue
            mine_neighbor = 0
            for j in (y-1, y, y+1):
                for i in (x-1, x, x+1):
                    if (0 <= i < num_cells_x) and (0 <= j < num_cells_y) and (not (i == x and j == y)):
                        mine_neighbor += cells[i + j * num_cells_x]['mine']
            cells[x + y * num_cells_x]['mine_neighbor'] = mine_neighbor


def uncover_cell(x, y):
    cell = cells[x + y * num_cells_x]
    if not cell['covered']:
        return
    cell['covered'] = False
    draw_cell(x, y)

    if not cell['mine'] and not cell['mine_neighbor']:
        for j in (y - 1, y, y + 1):
            for i in (x - 1, x, x + 1):
                if (0 <= i < num_cells_x) and (0 <= j < num_cells_y) and (not (i == x and j == y)):
                    uncover_cell(i, j)


def left_mouse_click(posx, posy):
    global game_in_playing
    if not game_in_playing:
        return

    x, y = cell_of_coordinate(posx, posy)
    if x < 0 or x >= num_cells_x or y < 0 or y >= num_cells_y:
        return

    cell = cells[x + y * num_cells_x]
    if cell['mine']:
        draw_smiley('sad_face.gif')
        game_in_playing = False
        cell['covered'] = False
        for y in range(num_cells_y):
            for x in range(num_cells_x):
                cell = cells[x + y * num_cells_x];
                if cell['mine'] ^ cell['flagged']:
                    draw_cell(x, y)
    else:
        # uncover a cell (and its neighbors)
        uncover_cell(x, y)


def right_mouse_click(posx, posy):
    global mine_remaining, game_in_playing
    if not game_in_playing:
        return

    x, y = cell_of_coordinate(posx, posy)
    if x < 0 or x >= num_cells_x or y < 0 or y >= num_cells_y:
        return
    cell = cells[x + y * num_cells_x]
    # toggle flag
    cell['flagged'] = not cell['flagged']
    # successfully flagged mine cell
    if cell['mine'] and cell['flagged']:
        mine_remaining -= 1
        if mine_remaining == 0:
            game_in_playing = False
            draw_smiley('cool_face.gif')

    draw_cell(x, y)


def start_game():
    global game_in_playing
    game_in_playing = True
    turtle.clear()
    create_game()
    draw_field()
    draw_smiley('smile_face.gif')


# setup turtle with no animation
turtle.setup()
turtle.mode('standard')

turtle.hideturtle()
turtle.speed('fastest')
turtle.tracer(n=1, delay=False)

for file in ['mine.gif', 'flag.gif']:
    from PIL import Image, ImageTk
    image = Image.open(file)
    image = (image.resize((cell_width, cell_height)))
    # create an object of PhotoImage
    shape = turtle.Shape('image', ImageTk.PhotoImage(image))
    turtle.register_shape(file, shape)

for file in ['smile_face.gif', 'cool_face.gif', 'sad_face.gif']:
    turtle.register_shape(file)

# listen to user inputs
turtle.onkeypress(start_game, 'space')
turtle.onscreenclick(left_mouse_click, btn=1)
turtle.onscreenclick(right_mouse_click, btn=3)
start_game()

turtle.listen()
turtle.mainloop()