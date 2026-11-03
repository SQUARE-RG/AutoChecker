struct Holder
{
    short narrow;
};

int main()
{
    Holder h{};
    long wideValue = 0L;
    h.narrow = static_cast<short>(wideValue);
    return 0;
}
