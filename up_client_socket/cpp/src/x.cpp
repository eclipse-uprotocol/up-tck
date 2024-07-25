#include <iostream>
#include <type_traits>
#include <optional>
#include <tuple>
#include <vector>
#include <array>

template <auto Start, auto End, auto Inc, class F>
constexpr void constexpr_for(F&& f)
{
    if constexpr (Start < End)
    {
        f(std::integral_constant<decltype(Start), Start>());
        constexpr_for<Start + Inc, End, Inc>(f);
    }
}

// template <typename T>
// struct is_optional : std::false_type {};

// template <typename T>
// struct is_optional<std::optional<T>> : std::true_type {};

// template <typename T>
// constexpr bool is_optional_v = is_optional<T>::value;

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::optional<T>& arg)
{
	if (arg != std::nullopt) os << *arg;
	else os << "nullopt";
	return os;
}

template <class... Args>
std::ostream& operator<<(std::ostream& os, const std::tuple<Args...>& t)
{
    // const auto len = 4;
    const auto len = std::tuple_size_v< std::tuple<Args...> >;
	constexpr_for<0, len, 1>([&](auto i) {
        os << ' ' << std::get<i>(t);
    });
	return os;
}

using namespace std;

using UUriKey = tuple<optional<string>, optional<uint32_t>, optional<uint32_t>, uint32_t >;

template <typename T>
void assign_if(T& field, size_t& cnt, size_t i, size_t bits)
{
    cout << "is not optional" << endl;
}

template <typename T>
void assign_if(optional<T>& field, size_t& cnt, size_t i, size_t bits)
{
    cout << "is optional" << endl;
    if (((1<<i) & bits) && (field != nullopt)) {
        field = nullopt;
        cnt++;
    }
}

vector<UUriKey> makeWildcardKeys(const UUriKey& key)
{
    const auto len = std::tuple_size_v<UUriKey>;
    vector<UUriKey> ret;
    ret.push_back(key);
    constexpr_for<1, len, 1>([&](const auto bits) {
        auto out = key;
        size_t cnt = 0;
        constexpr_for<0, len, 1>([&](const auto i) {
            assign_if(get<i>(out), cnt, i, bits);
            // if constexpr (is_optional_v<decltype(get<i>(key))>) {
            //     cout << "is optional" << endl;
            //     if (((1<<i) & bits) && (get<i>(out) != nullopt)) {
            //         get<i>(out) = nullopt;
            //         cnt++;
            //     }
            // }
            // else {
            //     cout << "is not optional" << endl;					
            // }
        });
        if (cnt > 0) {
            ret.push_back(out);
        }
    });
    return ret;
}

int main(int argc, char *argv[])
{
    // optional<int> x;
    // int y;

    // cout << is_optional_v<decltype(x)> << endl;
    // cout << is_optional_v<decltype(y)> << endl;

    UUriKey k{string{"hello"}, 1, 2, 3};
    cout << k << endl;
    auto v = makeWildcardKeys(k);
}