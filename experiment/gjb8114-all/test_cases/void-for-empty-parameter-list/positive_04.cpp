template <typename T>
T defaultValue(void) { return T{}; }

int main(void)
{
    int value = defaultValue<int>();
    return value == 0 ? 0 : 1;
}
