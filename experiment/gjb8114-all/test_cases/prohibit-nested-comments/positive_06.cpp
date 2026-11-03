#define FLAG 1

#if FLAG
int chosen_value = 5; /* a star * and a slash / remain separated */
#else
int chosen_value = /* fallback value */ 0;
#endif

int main()
{
    /* a standalone block comment */
    return chosen_value;
}
