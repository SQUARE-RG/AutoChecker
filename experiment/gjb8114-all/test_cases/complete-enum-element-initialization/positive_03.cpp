int main()
{
    enum Level
    {
        LOW = 0,
        MEDIUM = 5,
        HIGH = 10
    };
    Level l = MEDIUM;
    return static_cast<int>(l);
}
