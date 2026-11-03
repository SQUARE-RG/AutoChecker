char* copy_c_string(char* dest, const char* src)
{
    char* start = dest;
    while (*src != '\0') {
        *dest = *src;
        ++dest;
        ++src;
    }
    *dest = '\0';
    return start;
}

int main()
{
    char buffer[8];
    copy_c_string(buffer, "abc");
    return buffer[0];
}
