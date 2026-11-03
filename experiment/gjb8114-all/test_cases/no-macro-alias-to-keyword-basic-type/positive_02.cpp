#define APP_NAME "demo"
#define MAX_COUNT 10

int main()
{
    const char* name = APP_NAME;
    (void)name;
    int count = 0;
    for (int i = 0; i < MAX_COUNT; ++i)
    {
        count += 1;
    }
    return count == MAX_COUNT ? 0 : 1;
}
