typedef union U_Data
{
    unsigned char cd[4];
    int id;
} UData;

int main()
{
    UData uData;
    uData.id = 42;
    return uData.id;
}
