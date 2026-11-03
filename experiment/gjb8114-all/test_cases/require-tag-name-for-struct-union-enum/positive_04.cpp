enum class E_Level : int
{
    A_Level = 0,
    B_Level,
    C_Level,
    D_Level
};

int main()
{
    E_Level level = E_Level::B_Level;
    return static_cast<int>(level);
}
