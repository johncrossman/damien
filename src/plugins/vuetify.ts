import './main.scss'
import '@mdi/font/css/materialdesignicons.css'
import {aliases, mdi} from 'vuetify/iconsets/mdi-svg'
import {createVuetify} from 'vuetify'
import {VAppBar} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VAutocomplete} from 'vuetify/components/VAutocomplete'
import {VBanner} from 'vuetify/components/VBanner'
import {VBtn} from 'vuetify/components/VBtn'
import {VBtnToggle} from 'vuetify/components/VBtnToggle'
import {VCard, VCardActions, VCardSubtitle, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCheckbox} from 'vuetify/components/VCheckbox'
import {VChip} from 'vuetify/components/VChip'
import {VCol, VContainer, VSpacer, VRow} from 'vuetify/components/VGrid'
import {VCombobox} from 'vuetify/components/VCombobox'
import {VDataTable, VDataTableVirtual} from 'vuetify/components/VDataTable'
import {VDialog} from 'vuetify/components/VDialog'
import {VDivider} from 'vuetify/components/VDivider'
import {VExpansionPanel, VExpansionPanels, VExpansionPanelText, VExpansionPanelTitle} from 'vuetify/components/VExpansionPanel'
import {VFooter} from 'vuetify/components/VFooter'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VLayout} from 'vuetify/components/VLayout'
import {VList, VListItem, VListItemAction, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
import {VNavigationDrawer} from 'vuetify/components/VNavigationDrawer'
import {VProgressCircular} from 'vuetify/components/VProgressCircular'
import {VRadio} from 'vuetify/components/VRadio'
import {VRadioGroup} from 'vuetify/components/VRadioGroup'
import {VTable} from 'vuetify/components/VTable'
import {VTextarea} from 'vuetify/components/VTextarea'
import {VTextField} from 'vuetify/components/VTextField'
import {VSlideXReverseTransition, VSnackbar, VSwitch, VToolbar} from 'vuetify/components'

export default createVuetify({
  components: {
    VApp,
    VAppBar,
    VAutocomplete,
    VBanner,
    VBtn,
    VBtnToggle,
    VCard,
    VCardActions,
    VCardSubtitle,
    VCardText,
    VCardTitle,
    VCheckbox,
    VChip,
    VCol,
    VCombobox,
    VContainer,
    VDataTable,
    VDataTableVirtual,
    VDialog,
    VDivider,
    VExpansionPanel,
    VExpansionPanels,
    VExpansionPanelText,
    VExpansionPanelTitle,
    VFooter,
    VIcon,
    VImg,
    VLayout,
    VList,
    VListItem,
    VListItemAction,
    VListItemTitle,
    VMain,
    VMenu,
    VNavigationDrawer,
    VProgressCircular,
    VRadio,
    VRadioGroup,
    VRow,
    VSlideXReverseTransition,
    VSnackbar,
    VSpacer,
    VSwitch,
    VTable,
    VTextarea,
    VTextField,
    VToolbar
  },
  defaults: {
    VBtn: {
      flat: true,
      style: 'text-transform: none;',
    },
    VTextField: {
      density: 'compact',
      variant: 'outlined'
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi
    }
  },
  theme: {
    variations: {
      colors: ['anchor', 'error'],
      lighten: 2,
      darken: 2
    },
    themes: {
      light: {
        colors: {
          accent: '#CC4000',
          alert: '#FA9301',
          anchor: '#CC4000',
          background: '#FFF',
          disabled: '#BBCAD4',
          error: '#B71C1C',
          'evaluation-done': '#EBF8FF',
          'evaluation-done-label': '#176190',
          'evaluation-ignore': '#EBEBEB',
          'evaluation-ignore-label': '#666',
          'evaluation-to-do': '#F2FFF6',
          'evaluation-to-do-label': '#478047',
          'evaluation-xlisting': '#FFFFDD',
          hovered: '#EEE',
          muted: '#606060',
          'on-surface-variant': '#000',
          primary: '#125074',
          'primary-contrast': '#DAF0FD',
          secondary: '#307AAB',
          success: '#00C853',
          'surface-variant': '#F8F8F8',
          tertiary: '#307AAB',
          title: '#125074'
        }
      },
      dark: {
        colors: {
          accent: '#F04A00',
          alert: '#BB8009',
          anchor: '#F54E00',
          background: '#0D202C',
          disabled: '#BBCAD4',
          error: '#FF1414',
          'evaluation-done': '#001C2C',
          'evaluation-done-label': '#004A75',
          'evaluation-ignore': '#2D2D2D',
          'evaluation-ignore-label': '#666666',
          'evaluation-to-do': '#001E00',
          'evaluation-to-do-label': '#005400',
          'evaluation-xlisting': '#2B2600',
          hovered: '#616161',
          muted: '#BDBDBD',
          'on-surface-variant': '#FFF',
          primary: '#0C354D',
          'primary-contrast': '#94A8B3',
          secondary: '#1C4F72',
          success: '#00953E',
          'surface-bright': '#B0B0B0',
          'surface-variant': '#171717',
          tertiary: '#80BAE0',
          title: '#1E71A4'
        }
      }
    }
  }
})
