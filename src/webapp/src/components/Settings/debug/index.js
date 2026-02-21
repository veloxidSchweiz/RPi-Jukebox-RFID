import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Card,
  CardContent,
  CardHeader,
  Divider,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
  CircularProgress,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import request from '../../../utils/request';

const ConfigBlock = ({ name, file, data }) => (
  <Accordion variant="outlined" sx={{ mb: 0.5 }}>
    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
      <Typography variant="subtitle2">{name}</Typography>
      {file && (
        <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
          {file}
        </Typography>
      )}
    </AccordionSummary>
    <AccordionDetails>
      <Box
        component="pre"
        sx={{
          overflow: 'auto',
          maxHeight: 280,
          p: 1,
          bgcolor: 'action.hover',
          borderRadius: 1,
          fontSize: '0.75rem',
          fontFamily: 'monospace',
        }}
      >
        {JSON.stringify(data, null, 2)}
      </Box>
    </AccordionDetails>
  </Accordion>
);

const SettingsDebug = () => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchDebug = async () => {
      setLoading(true);
      setError(null);
      const { result, error: err } = await request('getDebugInfo');
      if (err) {
        setError(err);
        setData(null);
      } else {
        setData(result ?? null);
      }
      setLoading(false);
    };
    fetchDebug();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader title={t('settings.debug.title')} />
        <Divider />
        <CardContent sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
          <CircularProgress size={24} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader title={t('settings.debug.title')} />
        <Divider />
        <CardContent>
          <Typography color="error">{t('settings.debug.loading-error')}</Typography>
          <Typography variant="caption">{String(error)}</Typography>
        </CardContent>
      </Card>
    );
  }

  const plugins = data?.plugins ?? {};
  const loaded = plugins.loaded ?? {};
  const failed = plugins.failed ?? {};
  const details = plugins.details ?? {};
  const config = data?.config ?? {};
  const loadedNames = Object.keys(loaded);
  const failedNames = Object.keys(failed);

  return (
    <Card>
      <CardHeader title={t('settings.debug.title')} />
      <Divider />
      <CardContent>
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          {t('settings.debug.plugins.title')}
        </Typography>
        <List dense disablePadding>
          {loadedNames.map((name) => (
            <ListItem key={name} disableGutters sx={{ py: 0.25 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <CheckCircleIcon color="success" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={name}
                secondary={loaded[name] ?? null}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
              {details[name]?.has_config && (
                <Chip label={t('settings.debug.plugins.has-config')} size="small" sx={{ mr: 0.5 }} variant="outlined" />
              )}
              <Chip label={t('settings.debug.plugins.loaded')} size="small" color="success" variant="outlined" />
            </ListItem>
          ))}
          {failedNames.map((name) => (
            <ListItem key={`failed-${name}`} disableGutters sx={{ py: 0.25 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <ErrorIcon color="error" fontSize="small" />
              </ListItemIcon>
              <ListItemText
                primary={name}
                secondary={failed[name] ?? null}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
              <Chip label={t('settings.debug.plugins.failed')} size="small" color="error" variant="outlined" />
            </ListItem>
          ))}
          {loadedNames.length === 0 && failedNames.length === 0 && (
            <ListItem disableGutters>
              <ListItemText primary={t('settings.debug.plugins.none')} primaryTypographyProps={{ variant: 'body2' }} />
            </ListItem>
          )}
        </List>

        {loadedNames.some((name) => (details[name]?.callables?.length ?? 0) > 0) && (
          <>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }} gutterBottom>
              {t('settings.debug.callables.title')}
            </Typography>
            {loadedNames.map((name) => {
              const callables = details[name]?.callables ?? [];
              if (callables.length === 0) return null;
              return (
                <Accordion key={name} variant="outlined" sx={{ mb: 0.5 }} defaultExpanded={false}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="subtitle2">{name}</Typography>
                    <Chip size="small" label={callables.length} sx={{ ml: 1 }} />
                  </AccordionSummary>
                  <AccordionDetails sx={{ pt: 0 }}>
                    <List dense disablePadding>
                      {callables.map((c) => (
                        <ListItem key={c.fullname} disableGutters sx={{ flexDirection: 'column', alignItems: 'stretch' }}>
                          <Typography variant="caption" fontFamily="monospace" color="primary.main">
                            {c.fullname}{c.signature}
                          </Typography>
                          {c.description && (
                            <Typography variant="caption" color="text.secondary">
                              {c.description}
                            </Typography>
                          )}
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              );
            })}
          </>
        )}

        <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 2 }} gutterBottom>
          {t('settings.debug.config.title')}
        </Typography>
        <Box>
          {Object.keys(config).length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              {t('settings.debug.config.none')}
            </Typography>
          ) : (
            Object.entries(config).map(([name, { file, data: configData }]) => (
              <ConfigBlock key={name} name={name} file={file} data={configData} />
            ))
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default SettingsDebug;
