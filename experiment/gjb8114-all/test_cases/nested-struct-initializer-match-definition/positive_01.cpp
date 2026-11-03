struct Spixel
{
    unsigned int colour;
    struct Scoords
    {
        unsigned int x;
        unsigned int y;
    } coords;
};

int main(void)
{
    struct Spixel pixel = {1, {2, 3}};
    return (0);
}
