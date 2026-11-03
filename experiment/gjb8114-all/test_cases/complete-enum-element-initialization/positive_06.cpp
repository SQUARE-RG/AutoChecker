enum Sequence
{
    One = 1,
    Two = One + 1,
    Three = Two + 1
};

int main()
{
    Sequence value = Three;
    return static_cast<int>(value);
}
