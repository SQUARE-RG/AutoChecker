class Settings
{
public:
    signed int level : 3;
    unsigned int options : 5;
};

int main()
{
    Settings settings{};
    settings.level = -1;
    settings.options = 3u;
    return settings.level;
}
