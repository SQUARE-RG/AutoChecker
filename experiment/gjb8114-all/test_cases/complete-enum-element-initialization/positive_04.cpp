int main()
{
    enum class Mode
    {
        OFF = 0,
        ON,
        AUTO
    };
    Mode m = Mode::AUTO;
    return static_cast<int>(m);
}
