struct Spixel
{
    unsigned int colour;
    struct Scoords
    {
        unsigned int x;
        unsigned int y;
    } coords;
};

void draw(Spixel pixel)
{
    (void)pixel;
}

int main()
{
    draw({1, {2, 3}});
    return 0;
}
