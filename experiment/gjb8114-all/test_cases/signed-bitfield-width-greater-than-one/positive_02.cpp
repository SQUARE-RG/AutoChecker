struct Packed
{
    signed int first : 2, second : 3;
    unsigned int payload : 27;
};

int main()
{
    Packed packet{};
    packet.first = 0;
    packet.second = 0;
    return 0;
}
