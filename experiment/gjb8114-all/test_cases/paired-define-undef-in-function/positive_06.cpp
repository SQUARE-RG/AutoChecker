#define FILE_SCOPE_MACRO 3U

unsigned int get_value(void)
{
    return FILE_SCOPE_MACRO;
}

#undef FILE_SCOPE_MACRO

int main()
{
    return (get_value() == 3U) ? 0 : 1;
}
