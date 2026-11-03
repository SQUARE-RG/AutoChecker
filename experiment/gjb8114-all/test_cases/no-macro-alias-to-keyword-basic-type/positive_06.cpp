#define ENABLE_TRACE

int main()
{
    int result = 0;
#ifdef ENABLE_TRACE
    result = 1;
#endif
    return result;
}
