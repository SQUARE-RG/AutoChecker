struct StringHelper
{
    static const char* strstr(const char* haystack, const char* needle)
    {
        if (needle == nullptr || *needle == '\0') {
            return haystack;
        }
        return nullptr;
    }
};

int main()
{
    const char* result = StringHelper::strstr("abc", "b");
    (void)result;
    return 0;
}
