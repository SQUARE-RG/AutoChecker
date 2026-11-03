typedef enum E_Level
{
    A_Level = 0,
    B_Level,
    C_Level,
    D_Level
} eLevel;

int main()
{
    eLevel level = B_Level;
    return static_cast<int>(level);
}
