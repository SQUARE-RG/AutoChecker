struct Spixel
{
    unsigned int colour;
    struct Scoords
    {
        unsigned int x;
        unsigned int y;
    } coords;
};

Spixel pixel = {1, {2, 3}};

int main(void)
{
    return (0);
}
