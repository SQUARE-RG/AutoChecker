#define REPEAT_3(statement) do { statement; statement; statement; } while (false)

int main()
{
    int value = 0;
    REPEAT_3(++value);
    return value == 3 ? 0 : 1;
}
