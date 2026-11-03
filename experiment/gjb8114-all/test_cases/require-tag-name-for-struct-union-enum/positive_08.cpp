struct S_Container
{
    union U_Value
    {
        int id;
        unsigned char cd[4];
    } uData;
};

int main()
{
    S_Container container;
    container.uData.id = 7;
    return 0;
}
