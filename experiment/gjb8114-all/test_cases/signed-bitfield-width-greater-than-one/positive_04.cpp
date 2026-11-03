union PackedValue {
    signed int small : 2;
    unsigned int wide : 8;
};

int main(void)
{
    PackedValue value;
    value.small = -1;
    value.wide = 3;
    return 0;
}
