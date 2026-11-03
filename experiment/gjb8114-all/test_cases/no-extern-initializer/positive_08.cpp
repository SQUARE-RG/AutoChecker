enum Color { RED, GREEN };

extern Color g_color;
Color g_color = GREEN;

int main()
{
    g_color = RED;
    return 0;
}
