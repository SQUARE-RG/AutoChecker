template <typename T>
struct Flags
{
    signed short count : 4;
    unsigned short mode : 2;
    unsigned short reserved : 10;
    T payload;
};

int main()
{
    Flags<int> f{};
    f.count = 1;
    f.mode = 1;
    f.reserved = 0;
    f.payload = 0;
    return 0;
}
