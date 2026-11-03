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
    Spixel* pixel = new Spixel{1, {2, 3}};
    delete pixel;
    return 0;
}
