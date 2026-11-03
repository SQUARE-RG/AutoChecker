union Register
{
    struct Fields
    {
        signed long low : 8;
        unsigned long high : 8;
    } fields;
    unsigned int raw;
};

int main()
{
    Register reg;
    reg.fields.low = -1;
    reg.fields.high = 1;
    return 0;
}
