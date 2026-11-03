union U_Data
{
    unsigned char cd[4];
    int id;
} uData;

enum E_Level
{
    A_Level = 0,
    B_Level,
    C_Level,
    D_Level
} eLevel;

int main()
{
    eLevel = B_Level;
    uData.id = static_cast<int>(eLevel);
    return uData.id;
}
