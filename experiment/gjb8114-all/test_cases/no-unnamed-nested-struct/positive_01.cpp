struct Sdata
{
    unsigned char id;
    struct Scoor
    {
        unsigned char xs;
        unsigned char ys;
        unsigned char zs;
    } coor;
};

int main()
{
    Sdata data{};
    data.id = 1;
    data.coor.xs = 2;
    return 0;
}
