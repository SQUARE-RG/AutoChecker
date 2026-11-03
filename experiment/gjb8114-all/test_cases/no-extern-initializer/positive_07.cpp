extern volatile int g_count;
volatile int g_count = 7;

int main()
{
    g_count = 8;
    return 0;
}
