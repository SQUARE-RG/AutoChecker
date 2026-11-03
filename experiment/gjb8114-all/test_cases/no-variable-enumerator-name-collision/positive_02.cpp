enum Color { red, green, blue };

int main()
{
    int red_count = 0;
    for (int i = 0; i < 3; ++i) {
        int color_index = i;
        red_count += color_index;
    }
    Color c = green;
    (void)c;
    return red_count;
}
