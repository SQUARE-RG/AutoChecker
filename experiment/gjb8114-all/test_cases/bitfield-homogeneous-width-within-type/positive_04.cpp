struct Data4
{
    unsigned short a : 8;
    unsigned short b : 8;
    int normal_member;
    unsigned short c : 1;
    unsigned short d : 15;
};

int main()
{
    Data4 d{};
    return d.a + d.c;
}
