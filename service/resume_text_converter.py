from routers.schemas import LanguageLevel, ResumeToGovernment, SoftwareSkillLevel


class ResumeTextConverter:
    """Конвертирует резюме в форматированный текст для LLM.

    Example:
        converter = ResumeTextConverter()
        text = converter.convert(resume)
    """

    _LANGUAGE_LEVEL_MAP = {
        LanguageLevel.Native: "Родной",
        LanguageLevel.SpeakFluently: "Свободно владею",
        LanguageLevel.CanReadAndExplain: "Читаю и могу объяснить",
        LanguageLevel.ReadTranslateWithDict: "Читаю и перевожу со словарем",
    }

    _SOFTWARE_LEVEL_MAP = {
        SoftwareSkillLevel.Fluent: "Свободно",
        SoftwareSkillLevel.HaveGeneralIdea: "Общее представление",
        SoftwareSkillLevel.HaveNotSkill: "Не владею",
    }

    def convert(self, resume: ResumeToGovernment) -> str:
        """Преобразует резюме в форматированный текст с учетом пустых полей.

        Args:
            resume: Резюме в формате государственного кадрового резерва

        Returns:
            str: Форматированный текст резюме для передачи в LLM
        """
        sections = []

        main_info = []
        if not self._empty(resume.fullname):
            main_info.append(f"ФИО: {resume.fullname}")
        if not self._empty(resume.citizenship):
            main_info.append(f"Гражданство: {resume.citizenship}")
        if not self._empty(resume.passportOrEquivalent):
            main_info.append(f"Паспорт: {resume.passportOrEquivalent}")
        if not self._empty(resume.snils):
            main_info.append(f"СНИЛС: {resume.snils}")
        if not self._empty(resume.birthdate):
            main_info.append(f"Дата рождения: {resume.birthdate}")
        if not self._empty(resume.placeOfBirth):
            main_info.append(f"Место рождения: {resume.placeOfBirth}")
        if not self._empty(resume.registrationAddress):
            main_info.append(f"Адрес регистрации: {resume.registrationAddress}")
        if not self._empty(resume.actualResidenceAddress):
            main_info.append(f"Адрес проживания: {resume.actualResidenceAddress}")
        if not self._empty(resume.contactInformation):
            main_info.append(f"Контактная информация: {resume.contactInformation}")
        if not self._empty(resume.fullnameChange):
            main_info.append(f"Смена ФИО: {resume.fullnameChange}")
        if main_info:
            sections.append("ОСНОВНАЯ ИНФОРМАЦИЯ\n" + "\n".join(main_info))

        if not self._empty(resume.closeRelatives):
            relatives_section = ["БЛИЗКИЕ РОДСТВЕННИКИ"]
            for i, r in enumerate(resume.closeRelatives, 1):
                info = []
                if not self._empty(r.relationship):
                    info.append(f"Степень родства: {r.relationship}")
                if not self._empty(r.fullname):
                    info.append(f"ФИО: {r.fullname}")
                if not self._empty(r.birthdate):
                    info.append(f"Дата рождения: {r.birthdate}")
                if not self._empty(r.job):
                    info.append(f"Место работы: {r.job}")
                if not self._empty(r.address):
                    info.append(f"Адрес: {r.address}")
                if info:
                    relatives_section.append(f"{i}. " + "\n   ".join(info))
            if len(relatives_section) > 1:
                sections.append("\n".join(relatives_section))

        education_sections = []

        if not self._empty(resume.education.higherEducation):
            higher_ed = ["ВЫСШЕЕ ОБРАЗОВАНИЕ"]
            for i, edu in enumerate(resume.education.higherEducation, 1):
                info = []
                if not self._empty(edu.institutionName):
                    info.append(f"Учебное заведение: {edu.institutionName}")
                if not self._empty(edu.specialty):
                    info.append(f"Специальность: {edu.specialty}")
                if not self._empty(edu.level):
                    info.append(f"Уровень: {edu.level}")
                if not self._empty(edu.formOfEducation):
                    info.append(f"Форма обучения: {edu.formOfEducation}")
                if not self._empty(edu.year):
                    info.append(f"Год обучения: {edu.year}")
                if not self._empty(edu.haveDiploma):
                    info.append(
                        f"Наличие диплома: {'Да' if edu.haveDiploma else 'Нет'}"
                    )
                info.append(self._period(edu.dateOfAdmission, edu.dateOfGraduation))
                if info:
                    higher_ed.append(f"{i}. " + "\n   ".join(filter(None, info)))
            if len(higher_ed) > 1:
                education_sections.extend(higher_ed)

        if not self._empty(resume.education.additionalEducation):
            additional_ed = ["ДОПОЛНИТЕЛЬНОЕ ОБРАЗОВАНИЕ"]
            for i, edu in enumerate(resume.education.additionalEducation, 1):
                info = []
                if not self._empty(edu.institutionName):
                    info.append(f"Учебное заведение: {edu.institutionName}")
                if not self._empty(edu.educationalProgram):
                    info.append(f"Программа: {edu.educationalProgram}")
                if not self._empty(edu.programType):
                    info.append(f"Вид программы: {edu.programType}")
                if not self._empty(edu.hoursИumber):
                    info.append(f"Количество часов: {edu.hoursИumber}")
                info.append(self._period(edu.dateOfAdmission, edu.dateOfGraduation))
                if info:
                    additional_ed.append(f"{i}. " + "\n   ".join(filter(None, info)))
            if len(additional_ed) > 1:
                education_sections.extend(additional_ed)

        if not self._empty(resume.education.postgraduate):
            postgrad = ["ПОСЛЕВУЗОВСКОЕ ОБРАЗОВАНИЕ"]
            for i, edu in enumerate(resume.education.postgraduate, 1):
                info = []
                if not self._empty(edu.institutionName):
                    info.append(f"Учебное заведение: {edu.institutionName}")
                if not self._empty(edu.specialty):
                    info.append(f"Специальность: {edu.specialty}")
                if not self._empty(edu.degree):
                    info.append(f"Ученая степень: {edu.degree}")
                if not self._empty(edu.scienceBranch):
                    info.append(f"Отрасль наук: {edu.scienceBranch}")
                info.append(self._period(edu.dateOfAdmission, edu.dateOfGraduation))
                if info:
                    postgrad.append(f"{i}. " + "\n   ".join(filter(None, info)))
            if len(postgrad) > 1:
                education_sections.extend(postgrad)

        if education_sections:
            sections.append("ОБРАЗОВАНИЕ\n" + "\n".join(education_sections))

        if not self._empty(resume.languges):
            languages_section = ["ВЛАДЕНИЕ ЯЗЫКАМИ"]
            for lang in resume.languges:
                if not self._empty(lang.name) and not self._empty(lang.level):
                    level_text = self._LANGUAGE_LEVEL_MAP.get(
                        lang.level, lang.level.value
                    )
                    languages_section.append(f"- {lang.name}: {level_text}")
            if len(languages_section) > 1:
                sections.append("\n".join(languages_section))

        if not self._empty(resume.softwareSkills):
            skills_section = ["НАВЫКИ РАБОТЫ С КОМПЬЮТЕРОМ"]
            for skill in resume.softwareSkills:
                parts = []
                if not self._empty(skill.type):
                    parts.append(skill.type)
                if not self._empty(skill.nameOfProduct):
                    if parts:
                        parts[-1] += f": {skill.nameOfProduct}"
                    else:
                        parts.append(skill.nameOfProduct)
                if parts and not self._empty(skill.level):
                    level_text = self._SOFTWARE_LEVEL_MAP.get(
                        skill.level, skill.level.value
                    )
                    skills_section.append(f"- {' '.join(parts)} ({level_text})")
            if len(skills_section) > 1:
                sections.append("\n".join(skills_section))

        if not self._empty(resume.publications):
            pubs = [p for p in resume.publications if not self._empty(p)]
            if pubs:
                sections.append(
                    "НАУЧНЫЕ ТРУДЫ И ПУБЛИКАЦИИ\n"
                    + "\n".join(f"{i}. {p}" for i, p in enumerate(pubs, 1))
                )

        if not self._empty(resume.awards):
            awards = [a for a in resume.awards if not self._empty(a)]
            if awards:
                sections.append(
                    "ПРЕМИИ И НАГРАДЫ\n"
                    + "\n".join(f"{i}. {a}" for i, a in enumerate(awards, 1))
                )

        military_info = []
        if not self._empty(resume.militaryLiable):
            military_info.append(
                f"Военнообязанный: {'Да' if resume.militaryLiable else 'Нет'}"
            )
        if not self._empty(resume.militaryСategory):
            military_info.append(f"Годность: {resume.militaryСategory}")
        if military_info:
            sections.append("ВОИНСКАЯ ОБЯЗАННОСТЬ\n" + "\n".join(military_info))

        extra = []
        if not self._empty(resume.professionalInterests):
            extra.append(
                f"Сфера профессиональных интересов: {resume.professionalInterests}"
            )
        if not self._empty(resume.additionalInfo):
            extra.append(f"О себе: {resume.additionalInfo}")
        if not self._empty(resume.motivation):
            extra.append(f"Мотивация: {resume.motivation}")
        if not self._empty(resume.source):
            extra.append(f"Источник информации о резерве: {resume.source}")
        if extra:
            sections.append("ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ\n" + "\n".join(extra))

        return "\n\n".join(sections)

    @staticmethod
    def _empty(value) -> bool:
        """Проверяет, является ли значение пустым.

        Args:
            value: Любое значение

        Returns:
            bool: True если None, пустая строка или пустой список
        """
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False

    @staticmethod
    def _period(date_from: str, date_to: str) -> str:
        """Форматирует период обучения.

        Args:
            date_from: Дата начала
            date_to: Дата окончания

        Returns:
            str: Строка периода или пустая строка
        """
        if date_from and date_to:
            return f"Период: {date_from} - {date_to}"
        if date_from:
            return f"Дата поступления: {date_from}"
        if date_to:
            return f"Дата окончания: {date_to}"
        return ""
