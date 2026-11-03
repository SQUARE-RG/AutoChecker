#define DEFINE_ENUM(name) enum class name { Red, Green };

DEFINE_ENUM(Color)

int main()
{
    return static_cast<int>(Color::Green);
}
