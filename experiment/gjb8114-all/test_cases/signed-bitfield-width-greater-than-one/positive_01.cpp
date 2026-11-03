struct sData
{
    signed int si01 : 2;
    signed int si02 : 2;
    unsigned int serv : 28;
};

int main()
{
    sData my_data{};
    my_data.si01 = -1;
    my_data.si02 = -1;
    return 0;
}
