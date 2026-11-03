struct Flags
{
    unsigned enabled : 1;
    unsigned mode : 011 /* octal */;
};

int main()
{
    Flags flags{};
    flags.enabled = 1;
    return static_cast<int>(flags.mode);
}
