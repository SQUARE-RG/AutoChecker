struct Holder
{
    float value;
    explicit Holder(double d) : value(static_cast<float>(d)) {}
};

int main()
{
    Holder h(3.14);
    return 0;
}
