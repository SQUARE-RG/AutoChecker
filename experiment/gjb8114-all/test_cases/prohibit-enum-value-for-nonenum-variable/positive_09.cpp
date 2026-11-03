enum Mode { modeA = 1, modeB = 2 };

int main()
{
    Mode modes[2] = { modeA, modeB };
    unsigned int values[2] = { 3, 4 };
    values[0] = 5;
    values[1] = values[0] + 1;
    return static_cast<int>(modes[0]);
}
