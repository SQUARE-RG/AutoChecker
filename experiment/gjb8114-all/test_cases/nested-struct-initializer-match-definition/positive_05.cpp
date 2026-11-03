struct Spixel
{
    unsigned int colour;
    struct Scoords
    {
        unsigned int x;
        unsigned int y;
    } coords;
};

int main()
{
    Spixel pixel{1, {2, 3}};
    (void)pixel;
    return 0;
}
