typedef signed int SignedInt;

struct Data
{
    SignedInt value : 3;
    SignedInt other : 4;
};

int main()
{
    Data d{};
    d.value = -1;
    d.other = -1;
    return 0;
}
