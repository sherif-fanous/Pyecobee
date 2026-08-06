# Changelog

## [1.3.13] - 2026-07-31

### Fixed

- Skip unsupported API objects while deserializing a response ([`fc87b63`](https://github.com/sherif-fanous/Pyecobee/commit/fc87b63))

## [1.3.12] - 2022-01-13

### Added

- Add `fan_mode` to the `set_hold` function ([`77ef8b3`](https://github.com/sherif-fanous/Pyecobee/commit/77ef8b3))

## [1.3.11] - 2021-05-27

### Added

- Add `actual_voc`, `actual_co2`, `actual_aq_accuracy` and `actual_aq_score` to `Runtime` ([`3d6b4ae`](https://github.com/sherif-fanous/Pyecobee/commit/3d6b4ae))

### Fixed

- Fix deserialization of a response containing a missing or unrecognized attribute ([`3d6b4ae`](https://github.com/sherif-fanous/Pyecobee/commit/3d6b4ae))

## [1.3.10] - 2020-08-08

### Changed

- Format the code with Black instead of Autopep8

## [1.3.9] - 2020-08-04

### Added

- Add the undocumented `Energy` and `TimeOfUse` objects

### Changed

- Refactor and clean up the code with Autopep8 and Pylint

## [1.3.8] - 2020-08-01

### Added

- Add `fan_speed` to `Event`

## [1.3.7] - 2020-07-31

### Fixed

- Tolerate a property added by ecobee after this release instead of raising `KeyError`

## [1.3.6] - 2020-07-31

### Added

- Add `fan_speed` to `Settings`

## [1.3.5] - 2020-04-03

### Changed

- Refactor and clean up the code

## [1.3.0] - 2020-04-02

### Added

- Support every addition to the ecobee API since mid 2017

## [1.2.1] - 2017-06-01

### Changed

- Improve the internal use of `__slots__`

## [1.2.0] - 2017-05-31

### Changed

- Refactor the internals of `EcobeeObject` and `EcobeeResponse`

## [1.1.1] - 2017-05-31

### Changed

- Adjust internals so that PlantUML class diagrams can be generated automatically

## [1.1.0] - 2017-05-24

### Added

- Add the ecobee API operations that are accessible to EMS and Utility accounts only

## [1.0.0] - 2017-05-12

_First release, supporting every ecobee API operation except those accessible to EMS and Utility accounts only._

[1.3.13]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.13
[1.3.12]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.12
[1.3.11]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.11
[1.3.10]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.10
[1.3.9]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.9
[1.3.8]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.8
[1.3.7]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.7
[1.3.6]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.6
[1.3.5]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.5
[1.3.0]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.3.0
[1.2.1]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.2.1
[1.2.0]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.2.0
[1.1.1]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.1.1
[1.1.0]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.1.0
[1.0.0]: https://github.com/sherif-fanous/Pyecobee/releases/tag/v1.0.0
