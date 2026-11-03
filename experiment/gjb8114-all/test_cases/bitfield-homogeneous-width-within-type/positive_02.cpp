struct WordFlags
{
    unsigned int a : 8;
    unsigned int b : 8;
    unsigned int c : 8;
    unsigned int d : 8;
    unsigned int e : 5;
    unsigned int f : 11;
    unsigned int g : 16;
};

int main()
{
    WordFlags flags{};
    (void)flags;
    return 0;
}
