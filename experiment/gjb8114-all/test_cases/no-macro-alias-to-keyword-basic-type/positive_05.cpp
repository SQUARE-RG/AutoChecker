using Int64 = long long;

#define TO_STRING(x) #x

int main()
{
    Int64 value = 123;
    const char* text = TO_STRING(value);
    return text[0] == 'v' ? static_cast<int>(value) : 0;
}
